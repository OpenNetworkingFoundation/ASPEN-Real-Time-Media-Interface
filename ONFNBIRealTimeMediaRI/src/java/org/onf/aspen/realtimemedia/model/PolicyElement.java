/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.onf.aspen.realtimemedia.model;

import java.io.Serializable;
import java.util.List;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.xml.bind.annotation.XmlRootElement;

/**
 *
 * @author John Morey <jmorey@mmintl.com>
 */
@Entity
@XmlRootElement
public class PolicyElement implements Serializable {
    @Id
    @GeneratedValue(strategy=GenerationType.AUTO)    
    private String id;
    private List<FlowSpecElement> flowSpecElement;
    private RequestedQoS requestedQoS;
    private GrantedQoS grantedQoS;
    private String realm;

    /**
     * @return the id
     */
    public String getId() {
        return id;
    }

    /**
     * @param id the id to set
     */
    public void setId(String id) {
        this.id = id;
    }

    /**
     * @return the flowSpecElement
     */
    public List<FlowSpecElement> getFlowSpecElement() {
        return flowSpecElement;
    }

    /**
     * @param flowSpecElement the flowSpecElement to set
     */
    public void setFlowSpecElement(List<FlowSpecElement> flowSpecElement) {
        this.flowSpecElement = flowSpecElement;
    }

    /**
     * @return the requestedQoS
     */
    public RequestedQoS getRequestedQoS() {
        return requestedQoS;
    }

    /**
     * @param requestedQoS the requestedQoS to set
     */
    public void setRequestedQoS(RequestedQoS requestedQoS) {
        this.requestedQoS = requestedQoS;
    }

    /**
     * @return the grantedQoS
     */
    public GrantedQoS getGrantedQoS() {
        return grantedQoS;
    }

    /**
     * @param grantedQoS the grantedQoS to set
     */
    public void setGrantedQoS(GrantedQoS grantedQoS) {
        this.grantedQoS = grantedQoS;
    }

    /**
     * @return the realm
     */
    public String getRealm() {
        return realm;
    }

    /**
     * @param realm the realm to set
     */
    public void setRealm(String realm) {
        this.realm = realm;
    }
}
