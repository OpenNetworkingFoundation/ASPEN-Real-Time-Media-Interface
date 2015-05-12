/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.tmf.dsmapi.inventory.resource.model;

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

public class SessionElement implements Serializable {
    @Id
    @GeneratedValue(strategy=GenerationType.AUTO)    
    private String id;
    private List<MediaElement> mediaElement;
    private String startTime;
    private List<UserElement> userElement;
    private String sessionId;
    private String groupId;

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
     * @return the mediaElement
     */
    public List<MediaElement> getMediaElement() {
        return mediaElement;
    }

    /**
     * @param mediaElement the mediaElement to set
     */
    public void setMediaElement(List<MediaElement> mediaElement) {
        this.mediaElement = mediaElement;
    }

    /**
     * @return the startTime
     */
    public String getStartTime() {
        return startTime;
    }

    /**
     * @param startTime the startTime to set
     */
    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    /**
     * @return the userElement
     */
    public List<UserElement> getUserElement() {
        return userElement;
    }

    /**
     * @param userElement the userElement to set
     */
    public void setUserElement(List<UserElement> userElement) {
        this.userElement = userElement;
    }

    /**
     * @return the sessionId
     */
    public String getSessionId() {
        return sessionId;
    }

    /**
     * @param sessionId the sessionId to set
     */
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    /**
     * @return the groupId
     */
    public String getGroupId() {
        return groupId;
    }

    /**
     * @param groupId the groupId to set
     */
    public void setGroupId(String groupId) {
        this.groupId = groupId;
    }
}
